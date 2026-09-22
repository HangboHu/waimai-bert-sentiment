<script setup>
defineProps({ name: { type: String, required: true } });
const paths = {
  wave: 'M4 10v4m4-8v12m4-15v18m4-15v12m4-8v4',
  arrow: 'M5 12h14m-6-6 6 6-6 6',
  upload: 'M12 16V3m-5 5 5-5 5 5M4 15v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5',
  download: 'M12 3v13m-5-5 5 5 5-5M4 17v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3',
  close: 'm6 6 12 12M6 18 18 6',
};
</script>

<template>
  <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
    <path v-if="paths[name]" :d="paths[name]" />
    <template v-else-if="name === 'settings'">
      <path d="M4 7h9m4 0h3M4 17h3m4 0h9" />
      <circle cx="15" cy="7" r="2" /><circle cx="9" cy="17" r="2" />
    </template>
    <template v-else-if="name === 'search'">
      <circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" />
    </template>
    <template v-else-if="name === 'info'">
      <circle cx="12" cy="12" r="9" /><path d="M12 11v6m0-11v1" />
    </template>
  </svg>
</template>
