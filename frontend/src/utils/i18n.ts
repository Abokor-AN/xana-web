import { createI18n } from 'vue-i18n'

export const i18n = createI18n({
  locale: 'en',
  fallbackLocale: 'en',
  legacy: false,
  messages: {
    en: {
      the_world: 'the world'
    },
    fr: {
      the_world: 'le monde'
    }
  }
})
