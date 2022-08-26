<script lang="ts">
  import type { OutputImage } from "./types";

  export let images: OutputImage[] = [];
</script>

<section>
  {#each images as image}
    <a href={image.src} download={image.fileName}>
      <img alt="hi" src={image.src} width={image.width} height={image.height} />
    </a>
  {/each}
</section>

<style>
  section {
    min-width: 100%;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(512px, 512px));
    grid-gap: 1rem;
    justify-content: center;
  }
</style>
