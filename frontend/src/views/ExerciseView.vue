<template>
  <v-app>
    <v-main>
      <Exercise :level="level" />
    </v-main>
  </v-app>
</template>

<script setup>
import { defineProps } from 'vue';
import Exercise from '@/components/Exercise.vue';

const props = defineProps({
  level: Number
});

const level = props.level;
</script>