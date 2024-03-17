import { boot } from 'quasar/wrappers'
import axios from 'axios'
import { Buffer } from 'buffer'

const baseURL = 'http://localhost:8000/api/v1/'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
  baseURL: baseURL,
  timeout: 5000,
  headers: {
      'Authorization': localStorage.getItem('access_token') ? "JWT " + localStorage.getItem('access_token') : null,
      'Content-Type': 'application/json',
      'accept': 'application/json'
  }
})

api.interceptors.response.use(
  response => response,
  error => {
    const originalRequest = error.config
    // Prevent infinite loops
    if (error.response.status === 401 && originalRequest.url === baseURL+'token/refresh/') {
      window.location.href = '/login/'
      return Promise.reject(error)
    }

    if (error.response.data.code === "token_not_valid" &&
        error.response.status === 401 &&
        error.response.statusText === "Unauthorized")
    {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        const tokenParts = JSON.parse(Buffer.from(refreshToken.split('.')[1], 'base64').toString('utf8'))
        // exp date in token is expressed in seconds, while now() returns milliseconds:
        const now = Math.ceil(Date.now() / 1000)
        console.log(tokenParts.exp)
        if (tokenParts.exp > now) {
          return api
            .post('/jwt/refresh/', {refresh: refreshToken})
            .then((response) => {

              localStorage.setItem('access_token', response.data.access)
              localStorage.setItem('refresh_token', response.data.refresh)

              api.defaults.headers['Authorization'] = "JWT " + response.data.access
              originalRequest.headers['Authorization'] = "JWT " + response.data.access

              return api(originalRequest)
            })
            .catch(err => {
              console.log(err)
            });
        } else {
          console.log("Refresh token is expired", tokenParts.exp, now)
          window.location.href = '/login/'
        }
      } else {
        console.log("no refresh token")
        window.location.href = '/login/'
      }
    } // else error is different from 401
    return Promise.reject(error)
  }
)

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api }
