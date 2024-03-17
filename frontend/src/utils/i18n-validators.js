import * as validators from '@vuelidate/validators'
import { i18n } from 'boot/i18n'

const { createI18nMessage } = validators

const withI18nMessage = createI18nMessage({ t: i18n.global.t.bind(i18n) })

// wrap each validator.
export const required = withI18nMessage(validators.required)
export const email = withI18nMessage(validators.email)
// validators that expect a parameter should have `{ withArguments: true }` passed as a second parameter, to annotate they should be wrapped
export const minLength = withI18nMessage(validators.minLength, { withArguments: true })
// or you can provide the param at definition, statically
export const maxLength = withI18nMessage(validators.maxLength(10))
