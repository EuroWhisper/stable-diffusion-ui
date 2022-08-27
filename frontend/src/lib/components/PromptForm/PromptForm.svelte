<script lang="ts">
  import type { FormData } from "./types";

  let shouldDisplayConfig = false;

  let formData: FormData = {
    randomSeedChecked: true,
    seedValue: 343,
    promptValue: "",
    numBatchesValue: 1,
    numOutputsValue: 1,
    numInferenceStepsValue: 50,
    guidanceScaleValue: 75,
    widthValue: 512,
    heightValue: 512,
  };

  let guidanceScaleLabel = formData.guidanceScaleValue / 10;

  export let onGenerateClick: (formdata: FormData) => void;

  function updateGuidanceScale() {
    let guidanceScale = document.querySelector("#guidance_scale");
    let label = document.querySelector("#guidance_scale_value");
    guidanceScaleLabel = formData.guidanceScaleValue / 10;
  }

  function handlePromptChange(
    e: Event & {
      currentTarget: EventTarget & HTMLTextAreaElement;
    }
  ) {
    formData = {
      ...formData,
      promptValue: (e.target as HTMLTextAreaElement).value,
    };
  }

  function handleSeedChange(
    e: Event & {
      currentTarget: EventTarget & HTMLInputElement;
    }
  ) {
    formData = {
      ...formData,
      seedValue: parseInt((e.target as HTMLInputElement).value),
    };
  }

  function handleRandomSeedToggle() {
    formData = {
      ...formData,
      randomSeedChecked: !formData.randomSeedChecked,
    };
  }

  function handleNumBatchesChange(
    e: Event & {
      currentTarget: EventTarget & HTMLInputElement;
    }
  ) {
    formData = {
      ...formData,
      numBatchesValue: parseInt((e.target as HTMLInputElement).value),
    };
  }

  function handleNumOutputsChange(
    e: Event & {
      currentTarget: EventTarget & HTMLSelectElement;
    }
  ) {
    formData = {
      ...formData,
      numOutputsValue: parseInt((e.target as HTMLSelectElement).value),
    };
  }

  function handleWidthChange(
    e: Event & {
      currentTarget: EventTarget & HTMLSelectElement;
    }
  ) {
    formData = {
      ...formData,
      widthValue: parseInt((e.target as HTMLSelectElement).value),
    };
  }

  function handleHeightChange(
    e: Event & {
      currentTarget: EventTarget & HTMLSelectElement;
    }
  ) {
    formData = {
      ...formData,
      heightValue: parseInt((e.target as HTMLSelectElement).value),
    };
  }

  function handleNumInferenceStepsChange(
    e: Event & {
      currentTarget: EventTarget & HTMLInputElement;
    }
  ) {
    formData = {
      ...formData,
      numInferenceStepsValue: parseInt((e.target as HTMLInputElement).value),
    };
  }
</script>

<b>Prompt:</b><br />
<textarea
  on:change={handlePromptChange}
  id="prompt"
  placeholder="a photograph of an astronaut riding a horse"
/><br />

<div id="configHeader">
  <b>Advanced settings:</b> [<a
    on:click={() => {
      shouldDisplayConfig = true;
    }}
    id="configToggleBtn">show</a
  >]
</div>

{#if shouldDisplayConfig}
  <div id="config">
    <input id="sound_toggle" name="sound_toggle" type="checkbox" checked />
    <label for="sound_toggle">Enable Sound</label><br />
    <label for="seed">Seed:</label>
    <input
      on:change={handleSeedChange}
      type="number"
      id="seed"
      name="seed"
      value="30000"
    />
    <input
      on:input={handleRandomSeedToggle}
      id="random_seed"
      name="random_seed"
      type="checkbox"
      checked={formData.randomSeedChecked}
    /> <label for="random_seed">Random Image</label> <br />
    <label for="num_batches">Number of batches:</label>
    <input
      on:change={handleNumBatchesChange}
      type="number"
      id="num_batches"
      name="num_batches"
      value="1"
    /><br />
    <label for="num_outputs">Number of outputs:</label>
    <select
      on:change={handleNumOutputsChange}
      id="num_outputs"
      name="num_outputs"
      value="1"
      ><option value="1" selected>1</option><option value="4">4</option></select
    ><br />
    <label for="width">Width:</label>
    <select id="width" on:change={handleWidthChange} name="width" value="512"
      ><option value="128">128</option><option value="256">256</option><option
        value="512"
        selected>512</option
      ><option value="768">768</option><option value="1024">1024</option
      ></select
    ><br />
    <label for="height">Height:</label>
    <select id="height" on:change={handleHeightChange} name="height" value="512"
      ><option value="128">128</option><option value="256">256</option><option
        value="512"
        selected>512</option
      ><option value="768">768</option></select
    ><br />
    <label for="num_inference_steps">Number of inference steps:</label>
    <input
      id="num_inference_steps"
      on:change={handleNumInferenceStepsChange}
      name="num_inference_steps"
      value="50"
    /><br />
    <label for="guidance_scale">Guidance Scale:</label>
    <input
      on:change={updateGuidanceScale}
      id="guidance_scale"
      name="guidance_scale"
      value="75"
      type="range"
      min="10"
      max="200"
    /> <span id="guidance_scale_value">{guidanceScaleLabel}</span><br />
  </div>
{/if}

<button on:click={() => onGenerateClick(formData)} id="makeImage"
  >Make Image</button
>
