<script>

  const HEALTH_PING_INTERVAL = 5 // seconds
  
  let serverStatus = 'offline'
  let images = [];
  let shouldDisplayConfig = false;
  let randomSeedChecked = true;
  let seedValue = 343;
  let promptValue = "";
  let numBatchesValue = 1;
  let numOutputsValue = 1;
  let numInferenceStepsValue = 50;
         let guidanceScaleValue = 75;
        let  widthValue = 512;
        let  heightValue = 512;
  function setStatus(statusType, msg, msgType) {
      let el = ''
  
      if (statusType === 'server') {
          el = '#serverStatus'
          serverStatus = msg
      } else if (statusType === 'request') {
          el = '#reqStatus'
      }
  
      if (msgType == 'error') {
          msg = '<span style="color: red">' + msg + '<span>'
      } else if (msgType == 'success') {
          msg = '<span style="color: green">' + msg + '<span>'
      }
  
      if (el) {
          document.querySelector(el).innerHTML = msg
      }
  }
  
  function playSound() {
      const audio = new Audio('/media/ding.mp3')
      audio.volume = 0.2
      audio.play()
  }
  
  async function healthCheck() {
      try {
          let res = await fetch('http://localhost:8000/ping')
          res = await res.json()
  
          if (res[0] == 'OK') {
              setStatus('server', 'online', 'success')
          } else {
              setStatus('server', 'offline', 'error')
          }
      } catch (e) {
          setStatus('server', 'offline', 'error')
      }
  }
  
  async function makeImage() {
    console.log("Making image");
      setStatus('request', 'fetching..')
  
      let btn = document.querySelector('#makeImage')
      btn.innerHTML = 'Processing..'
      btn.disabled = true;
  
      let outputMsg = document.querySelector('#outputMsg')
      outputMsg.innerHTML = 'Fetching..'
  
      function logError(msg, res) {
          outputMsg.innerHTML = '<span style="color: red">Error: ' + msg + '</span>'
          console.log('request error', res)
          setStatus('request', 'error', 'error')
      }
  
      let seed = (randomSeedChecked ? Math.floor(Math.random() * 10000) : seedValue)
  
      let reqBody = {
          prompt: promptValue,
          num_outputs: numOutputsValue,
          num_inference_steps: numInferenceStepsValue,
          guidance_scale: guidanceScaleValue / 10,
          width: widthValue,
          height: heightValue,
          seed: seed,
      }
      console.log(reqBody);
      let res = ''
      let time = new Date().getTime()
  
      try {
          res = await fetch('http://localhost:8000/image', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(reqBody)
          })
  
          if (res.status != 200) {
              if (serverStatus === 'online') {
                  logError('Stable Diffusion had an error: ' + await res.text() + '. This happens sometimes. Maybe modify the prompt or seed a little bit?', res)
              } else {
                  logError("Stable Diffusion is still starting up, please wait. If this goes on beyond a few minutes, Stable Diffusion has probably crashed.", res)
              }
              res = undefined
          } else {
              res = await res.json()
  
              if (res.status !== 'succeeded') {
                  let msg = ''
                  if (res.detail !== undefined) {
                      msg = res.detail[0].msg + " in " + JSON.stringify(res.detail[0].loc)
                  } else {
                      msg = res
                  }
                  logError(msg, res)
                  res = undefined
              }
          }
      } catch (e) {
          console.log('request error', e)
          setStatus('request', 'error', 'error')
      }
  
      btn.innerHTML = 'Make Image'
      btn.disabled = false;
  
  
      // const shouldPlaySound = document.querySelector('#sound_toggle').checked
  
      // if (shouldPlaySound) {
      //     playSound()
      // }
  
      if (!res) {
          return
      }
  
      time = new Date().getTime() - time
      time /= 1000
  
      outputMsg.innerHTML = 'Processed in ' + time + ' seconds. Seed: ' + seed
  
      for (let idx in res.output) {
          let imgBody = ''
  
          try {
              imgBody = res.output[idx]
          } catch (e) {
              console.log(imgBody)
              setStatus('request', 'invalid image', 'error')
              return
          }
  
          let img = {};
          img.width = parseInt(reqBody.width)
          img.height = parseInt(reqBody.height)
          img.src = imgBody
          images = [...images, img];
          console.log(images);
      }
  
      setStatus('request', 'done', 'success')
  
      // if (random_seed.checked) {
      //     let seedEl = document.querySelector("#seed")
      //     seedEl.value = seed
      // }

  }
  
  async function handleMakeImage() {
      images = [];

      const numBatches = 10; 
  
      for(let i = 0; i < numBatches; i++) {
          await makeImage();
      }
  }
    
  
 
  

  function updateGuidanceScale() {
    let guidanceScale = document.querySelector('#guidance_scale')
      let label = document.querySelector('#guidance_scale_value')
      label.innerHTML = guidanceScale.value / 10
  }
  
  
  let random_seed = document.querySelector("#random_seed")
  function checkRandomSeed() {
      let seed = document.querySelector("#seed")
      if (random_seed.checked) {
          seed.disabled = true
          seed.value = "random"
      } else {
          seed.disabled = false
      }
  }
  
  setInterval(healthCheck, HEALTH_PING_INTERVAL * 1000)
  </script>


<main>
  <h3>Stable Diffusion - Quick UI</h3>

  <div id="status">Server status: <span id="serverStatus">checking..</span> | Request status: <span id="reqStatus">n/a</span></div>

  <br/>

  <b>Prompt:</b><br/>
  <textarea on:change={(e) => promptValue = e.target.value} id="prompt" placeholder="a photograph of an astronaut riding a horse" ></textarea><br/>

  <div id="configHeader"><b>Advanced settings:</b> [<a on:click={() => {shouldDisplayConfig = true}} id="configToggleBtn" href="#">show</a>]</div>
  {#if shouldDisplayConfig}
  <div id="config">
      <input id="sound_toggle" name="sound_toggle" type="checkbox" checked> <label for="sound_toggle">Enable Sound</label><br/>
      <label for="seed">Seed:</label> <input on:change={(e) => seedValue = e.target.value} id="seed" name="seed" value="30000"> <input on:input={checkRandomSeed} id="random_seed" name="random_seed" type="checkbox" checked={randomSeedChecked}> <label for="random_seed">Random Image</label> <br/>
      <label for="num_batches">Number of batches:</label> <input on:change={(e) => numBatchesValue = e.target.value} type="number" id="num_batches" name="num_batches" value="1" /><br/>
      <label for="num_outputs">Number of outputs:</label> <select on:change={(e) => numOutputsValue = e.target.value} id="num_outputs" name="num_outputs" value="1"><option value="1" selected>1</option><option value="4">4</option></select><br/>
      <label for="width">Width:</label> <select id="width" on:change={(e) => widthValue = e.target.value} name="width" value="512"><option  value="128">128</option><option value="256">256</option><option value="512" selected>512</option><option value="768">768</option><option value="1024">1024</option></select><br/>
      <label for="height">Height:</label> <select id="height" on:change={(e) => heightValue = e.target.value} name="height" value="512"><option value="128">128</option><option value="256">256</option><option value="512" selected>512</option><option value="768">768</option></select><br/>
      <label for="num_inference_steps">Number of inference steps:</label> <input id="num_inference_steps" on:change={(e) => numInferenceStepsValue = e.target.value} name="num_inference_steps" value="50"><br/>
      <label for="guidance_scale">Guidance Scale:</label> <input on:change={updateGuidanceScale} id="guidance_scale" name="guidance_scale" value="75" type="range" min="10" max="200"> <span id="guidance_scale_value"></span><br/>
  </div>
  {/if}

  <button on:click={handleMakeImage} id="makeImage">Make Image</button> <br/><br/>

  <div id="outputMsg"></div>

  <div id="images">
    {#each images as image}
    <img alt="hi" src={image.src} width={image.width} height={image.height} />
    {/each}
  </div>

  <div id="footer">
      <p>Please feel free to <a href="https://github.com/cmdr2/stable-diffusion-ui/issues" target="_blank">file an issue</a> or <a href="mailto:sd@cmdr2.org" target="_blank">email me</a> if you have any problems or suggestions in using this interface.</p>
      <p><b>Disclaimer:</b> I am not responsible for any images generated using this interface.</p>
  </div>
</main>

<style>
  #prompt {
      width: 50vw;
      height: 50pt;
  }
  @media screen and (max-width: 600px) {
      #prompt {
          width: 95%;
      }
  }
  #configHeader {
      margin-top: 5px;
      margin-bottom: 5px;
      font-size: 10pt;
  }
  #config {
      font-size: 9pt;
      margin-bottom: 5px;
      padding-left: 10px;
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
