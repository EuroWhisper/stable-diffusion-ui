<script lang="ts">
  import OutputImages from "./lib/components/OutputImages/OutputImages.svelte";
  import { v4 as uuidv4 } from "uuid";
  import type { OutputImage } from "./lib/components/OutputImages/types";
  import LoadingSpinner from "./lib/components/LoadingSpinner.svelte";
  import PromptForm from "./lib/components/PromptForm/PromptForm.svelte";
  import type { FormData } from "./lib/components/PromptForm/types";

  const HEALTH_PING_INTERVAL = 35; // seconds

  let serverStatus = "offline";
  let generatingImages = false;
  let images = [];

  function setStatus(statusType, msg, msgType) {
    let el = "";

    if (statusType === "server") {
      el = "#serverStatus";
      serverStatus = msg;
    } else if (statusType === "request") {
      el = "#reqStatus";
    }

    if (msgType == "error") {
      msg = '<span style="color: red">' + msg + "<span>";
    } else if (msgType == "success") {
      msg = '<span style="color: green">' + msg + "<span>";
    }

    if (el) {
      document.querySelector(el).innerHTML = msg;
    }
  }

  function playSound() {
    const audio = new Audio("/media/ding.mp3");
    audio.volume = 0.2;
    audio.play();
  }

  async function healthCheck() {
    try {
      let res = await fetch("http://localhost:8000/ping");
      res = await res.json();

      if (res[0] == "OK") {
        setStatus("server", "online", "success");
      } else {
        setStatus("server", "offline", "error");
      }
    } catch (e) {
      setStatus("server", "offline", "error");
    }
  }

  async function makeImage(formData: FormData) {
    generatingImages = true;

    let outputMsg = document.querySelector("#outputMsg");
    outputMsg.innerHTML = "Fetching..";

    function logError(msg, res) {
      outputMsg.innerHTML =
        '<span style="color: red">Error: ' + msg + "</span>";
      console.log("request error", res);
      setStatus("request", "error", "error");
    }

    let seed = formData.randomSeedChecked
      ? Math.floor(Math.random() * 10000)
      : formData.seedValue;

    let reqBody = {
      prompt: formData.promptValue,
      num_outputs: formData.numOutputsValue,
      num_inference_steps: formData.numInferenceStepsValue,
      guidance_scale: formData.guidanceScaleValue / 10,
      width: formData.widthValue,
      height: formData.heightValue,
      seed: formData.seedValue,
    };
    console.log(reqBody);
    let time = new Date().getTime();
    let res;
    try {
      res = await fetch("http://localhost:8000/image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(reqBody),
      });

      if (res.status != 200) {
        if (serverStatus === "online") {
          logError(
            "Stable Diffusion had an error: " +
              (await res.text()) +
              ". This happens sometimes. Maybe modify the prompt or seed a little bit?",
            res
          );
        } else {
          logError(
            "Stable Diffusion is still starting up, please wait. If this goes on beyond a few minutes, Stable Diffusion has probably crashed.",
            res
          );
        }
        res = undefined;
      } else {
        res = await res.json();

        if (res.statusText !== "succeeded") {
          let msg = "";
          if (res.detail !== undefined) {
            msg =
              res.detail[0].msg + " in " + JSON.stringify(res.detail[0].loc);
          } else {
            msg = res;
          }
          logError(msg, res);
          res = undefined;
        }
      }
    } catch (e) {
      console.log("request error", e);
    }

    // const shouldPlaySound = document.querySelector('#sound_toggle').checked

    // if (shouldPlaySound) {
    //     playSound()
    // }

    if (!res) {
      return;
    }

    time = new Date().getTime() - time;
    time /= 1000;

    outputMsg.innerHTML = "Processed in " + time + " seconds. Seed: " + seed;

    for (let idx in res.output) {
      let imgBody = "";

      try {
        imgBody = res.output[idx];
      } catch (e) {
        console.log(imgBody);
        setStatus("request", "invalid image", "error");
        return;
      }

      let img: OutputImage = {
        id: uuidv4(),
        width: reqBody.width,
        height: reqBody.height,
        src: imgBody,
        seed,
        fileName: `${formData.promptValue.substring(
          0,
          50
        )}_seed_${seed}_${uuidv4()}`,
      };

      images = [...images, img];
      console.log(images);
    }
    generatingImages = false;
    setStatus("request", "done", "success");

    // if (random_seed.checked) {
    //     let seedEl = document.querySelector("#seed")
    //     seedEl.value = seed
    // }
  }

  async function handleMakeImage(formData: FormData) {
    images = [];

    for (let i = 0; i < formData.numBatchesValue; i++) {
      await makeImage(formData);
    }
  }

  setInterval(healthCheck, HEALTH_PING_INTERVAL * 1000);
</script>

<main>
  <h3>Stable Diffusion - Svelte UI</h3>

  <div id="status">
    Server status: <span id="serverStatus">checking..</span> | Request status:
    <span id="reqStatus">n/a</span>
  </div>

  <br />
  <PromptForm {generatingImages} onGenerateClick={handleMakeImage} />
  <br /><br />

  <div id="outputMsg" />

  {#if generatingImages}
    <div class="spinner-wrapper">
      <LoadingSpinner />
    </div>
  {/if}

  <OutputImages {images} />

  <div id="footer">
    <p>
      <b>Disclaimer:</b> I am not responsible for any images generated using this
      interface.
    </p>
  </div>
</main>

<style>
  .spinner-wrapper {
    margin-top: 2rem;
    width: 100%;
    display: flex;
    justify-content: center;
  }
  #outputMsg {
    font-size: small;
  }
  #footer {
    margin-top: 5px;
    padding-top: 5px;
    font-size: small;
  }
</style>
