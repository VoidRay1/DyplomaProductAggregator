import { gql } from '@apollo/client'

export const TOKEN_AUTH = gql`
  mutation tokenAuth ($email: String!, $password: String!) {
    tokenAuth(
      email: $email
      password: $password
    ) {
      token
      refreshToken
    }
  }
`;

export const REFRESH_TOKEN = gql`
  mutation refreshToken ($refreshToken: String!) {
    refreshToken(refreshToken: $refreshToken) {
      token
      refreshToken
    }
  }
`;

export const REVOKE_TOKEN = gql`
  mutation revokeToken ($refreshToken: String) {
    revokeToken(
      refreshToken: $refreshToken
    ) {
      revoked
    }
  }
`;

export const profileFragment = gql`
  fragment ProfileFields on ProfileType {
    avatar
    firstName
    lastName
    dateOfBirth
    country
    telegramUsername
  }
`;

export const GET_USER = gql`
  query getUser {
    viewer {
      id
      username
      email
      phone
      locale
      profile {
        ...ProfileFields
      }
      preferences {
        section
        name
        value
      }
    }
  }
  ${profileFragment}
`;

export const SET_USER = gql`
  mutation updateProfile ($user: UserInput!) {
    updateProfile(input: $user) {
      ok
      user {
        username
        email
        phone
        profile {
          ...ProfileFields
        }
      }
    }
  }
  ${profileFragment}
`;

export const GET_PREFERENCES = gql`
  query getPreferences ($language: String) {
    preferences(language: $language) {
      section
      name
      value
      verboseName
      helpText
      field {
        inputType
      }
    }
  }
`;

export const SET_PREFERENCES = gql`
  mutation updatePreferences ($items: [ItemPreference]!) {
    updatePreferences(input: $items) {
      ok
    }
  }
`;

export const UPLOAD_PHOTO = gql`
  mutation uploadPhoto($file: Upload!) {
    uploadPhoto(file: $file) {
      ok
#      filename
#      path
    }
  }
`;

export const GET_TAGS = gql`
  query getTags ($category: Int, $language: String) {
    tags(category: $category, language: $language) {
      slug
      category
      tag(language: $language)
    }
  }
`;

export const GET_SHOPS = gql`
  query getShops ($country: String!, $language: String) {
    shops (country: $country, language: $language) {
      id
      title
      description
      image
      url
      active
    }
  }
`;

export const GET_SHOP_CATEGORIES = gql`
  query getShopCategories ($shop: ID!, $parent: String, $filters: ShopFilterInput, $slug: String, $language: String) {
    shopCategories (
      shop: $shop
      parent: $parent
      filters: $filters
      slug: $slug
      language: $language
    ) {
      id
      name
      categorySlug
      countProducts
      parent {
        id
        categorySlug
      }
    }
  }
`;

export const GET_SHOP_PRODUCTS = gql`
  query getShopProducts ($shop: ID!, $category: String, $filters: ShopFilterInput, $sortBy: String, $sortDirection: String, $slug: String, $language: String, $first: Int, $after: String) {
    shopProducts (
      shop: $shop
      category: $category
      filters: $filters
      sortBy: $sortBy
      sortDirection: $sortDirection
      slug: $slug
      language: $language
      first: $first
      after: $after
    ) {
      edges {
        cursor
        node {
          id
          url
          image
          name
          brand
          volume
          price {
            price
            currency
            oldPrice
            discount
            percent
            available
            promotions {
              edges {
                node {
                  id
                  iconUrl
                  title
                }
              }
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
`;

export const GET_SHOP_FILTERS = gql`
query getShopFilters ($shop: ID!, $category: String, $language: String) {
  shopFilters (shop: $shop, category: $category, language: $language) {
    filters {
      __typename
      ... on RangeNode {
        min
        max
        param
      }
      __typename
      ... on ListNode {
        param
        values {
          value
          count
        }
      }
    }
  }
}
`;