import { HttpLink, ApolloLink, ApolloClient, InMemoryCache, fromPromise } from '@apollo/client/core'
import { createUploadLink } from 'apollo-upload-client'
import { onError } from '@apollo/client/link/error'
import { offsetLimitPagination, relayStylePagination, Observable } from '@apollo/client/utilities'
import { GraphQLError } from 'graphql'
import { REFRESH_TOKEN } from '../constants/graphql'

export /* async */ function getClientOptions(/* {app, router, ...} */ options) {

  const graphqlUrl = process.env.GRAPHQL_URI ||
    // Change to your graphql endpoint.
    'http://localhost:8000/graphql'

  const httpLink = new HttpLink({
    uri: graphqlUrl,
    //credentials: 'same-origin'
  })

  // add the authorization to the headers
  const token = localStorage.getItem('access_token')
  let headers = {
    authorization: token ? `JWT ${token}` : ""
  }

  const httpOptions = {
    uri: graphqlUrl,
    headers: headers,
  }
  
  let isRefreshing = false
  let pendingRequests = []

  const resolvePendingRequests = () => {
    pendingRequests.map(callback => callback())
    pendingRequests = []
  }
  
  const errorLink = onError(
    ({ graphQLErrors, networkError, operation, response, forward }) => {
      if (graphQLErrors) {
        for (let err of graphQLErrors) {
          if (err.message.includes('Signature has expired')
            || err.message.includes('There is no current event loop in thread'
            || response.data[operation.operationName]?.__typename.includes('Signature has expired'))
          ) {
            // ignore 401 error for a refresh request
            if (operation.operationName === 'refreshToken') return

            if (!isRefreshing) {
              const observable = new Observable(
                (observer) => {
                  // used an annonymous function for using an async function
                  (async () => {
                    try {
                      const accessToken = await refreshToken()
                      if (!accessToken) {
                        throw new GraphQLError('Empty AccessToken')
                      }
                      headers = {
                        authorization: `JWT ${accessToken}`
                      }
                      // Retry the failed request
                      const subscriber = {
                        next: observer.next.bind(observer),
                        error: observer.error.bind(observer),
                        complete: observer.complete.bind(observer),
                      }
                      forward(operation).subscribe(subscriber)
                    } catch (err) {
                      localStorage.clear()
                      observer.error(err)
                    }
                  })()
                }
              )
              return observable
            } else {
              // Will only emit once the Promise is resolved
              let forward$ = fromPromise(
                new Promise(resolve => {
                  pendingRequests.push(() => resolve())
                })
              )
              return forward$.flatMap(() => forward(operation))
            }
          }
        }
      }
  
      if (networkError) console.log(`[Network error]: ${networkError}`)
    }
  )

  const authMiddleware = new ApolloLink((operation, forward) => {
    // console.log(operation.operationName)
    if (operation.operationName === 'refreshToken')
      return forward(operation)

    operation.setContext({
      headers: headers
    })
    return forward(operation)
  })

  const uploadLink = ApolloLink.split(
    (operation) => operation.getContext().hasUpload,
    createUploadLink(httpOptions),
    ApolloLink.from([errorLink, authMiddleware, httpLink])//new BatchHttpLink(httpOptions)
  )

  const cache = new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          searchProducts: relayStylePagination(['query']),
          shopProducts: relayStylePagination(['shop', 'filters', 'sortBy', 'sortDirection']),
          searchShopProducts: relayStylePagination(['shop', 'query', 'filters', 'sortBy', 'sortDirection']),
        }
      },
    },
  });

  const apolloClient = new ApolloClient({
    cache,
    link: uploadLink,
  })

  // Request a refresh token to then stores and returns the accessToken.
  const refreshToken = async () => {
    try {
      isRefreshing = true
      const res = await apolloClient.mutate({
        mutation: REFRESH_TOKEN,
        variables: {
          refreshToken: localStorage.getItem('refresh_token')
        }
      })
      const accessToken = res.data?.refreshToken?.token
      const refreshToken = res.data?.refreshToken?.refreshToken
      localStorage.setItem('access_token', accessToken || '')
      localStorage.setItem('refresh_token', refreshToken || '')
      headers = {
        authorization: `JWT ${accessToken}`
      }
      resolvePendingRequests()
      return accessToken
    } catch (err) {
      localStorage.clear()
      pendingRequests = []
      throw err
    } finally {
      isRefreshing = false
    }
  }

  return Object.assign(
    // General options.
    {
      link: apolloClient.link,
      cache: apolloClient.cache,
    },
    // Specific Quasar mode options.
    process.env.MODE === 'spa'
      ? {
          //
        }
      : {},
    process.env.MODE === 'ssr'
      ? {
          //
        }
      : {},
    process.env.MODE === 'pwa'
      ? {
          //
        }
      : {},
    process.env.MODE === 'bex'
      ? {
          //
        }
      : {},
    process.env.MODE === 'cordova'
      ? {
          //
        }
      : {},
    process.env.MODE === 'capacitor'
      ? {
          //
        }
      : {},
    process.env.MODE === 'electron'
      ? {
          //
        }
      : {},
    // dev/prod options.
    process.env.DEV
      ? {
          //
        }
      : {},
    process.env.PROD
      ? {
          //
        }
      : {},
    // For ssr mode, when on server.
    process.env.MODE === 'ssr' && process.env.SERVER
      ? {
          ssrMode: true,
        }
      : {},
    // For ssr mode, when on client.
    process.env.MODE === 'ssr' && process.env.CLIENT
      ? {
          ssrForceFetchDelay: 100,
        }
      : {}
  )
}
