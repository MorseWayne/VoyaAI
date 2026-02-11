<script setup>
import { computed } from 'vue'
import SectionWeather from './SectionWeather.vue'
import SectionTimeline from './SectionTimeline.vue'
import SectionCommute from './SectionCommute.vue'
import SectionExpenses from './SectionExpenses.vue'
import SectionText from './SectionText.vue'

const props = defineProps({
  guide: {
    type: Object,
    required: true
  }
})

const getComponent = (type) => {
  switch (type) {
    case 'weather': return SectionWeather
    case 'timeline': return SectionTimeline
    case 'commute': return SectionCommute
    case 'expenses': return SectionExpenses
    case 'info': return SectionText // Info usually just text lists, reusing text for now or custom
    default: return SectionText
  }
}
</script>

<template>
  <div class="space-y-8">
    <div v-for="(section, index) in guide.sections" :key="index">
      <component 
        :is="getComponent(section.type)" 
        :section="section" 
      />
    </div>
  </div>
</template>
