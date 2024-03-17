import { boot } from 'quasar/wrappers'
import { createGettext } from 'vue3-gettext'
import translations from '../language/translations.json'

export default boot(({ app }) => {
  const gettext = createGettext({
    availableLanguages: {
      en: 'English',
      uk: 'Українська',
      ru: 'Русский',
    },
    defaultLanguage: 'en',
    translations: translations,
    setGlobalProperties: true,
    globalProperties: {
      gettext: ['$gettext', '__'],  // both support `$gettext`, `__` the two names
      ngettext: ['$ngettext', '_n'],
      pgettext: ['$pgettext', '_x'],
      npgettext: ['$npgettext', '_nx'],
    }
  })

  // Set gettext instance on app
  app.use(gettext)
})
