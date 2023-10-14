// Composables
import { createRouter, createWebHistory } from 'vue-router'
import { hook } from './helpers'
import { auth } from '@/store/auth'
import { NavigationClient } from '@azure/msal-browser'

const unmatched = '/:pathMatch(.*)*'
const unguarded = [
  '/',
  '/login',
  '/logout',
  '/signin',
  '/welcome'
]

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "home" */ '@/views/Home.vue'),
      },
      {
        path: 'welcome',
        name: 'Welcome Page',
        component: () => import(/* webpackChunkName: "home" */ '@/views/Welcome.vue'),
      }
    ],
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})



/// AUTHENTICATION

// hook MSAL into router
const client = new NavigationClient()

// set up auth and guard routes
router.beforeEach(async (to, from, next) => {
  // 404
  if (to.matched[0]?.path === unmatched) {
    return next()
  }

  // guarded
  const guarded = unguarded.every(path => path !== to.path)
  if (guarded) {
    // initialized
    if (!auth.initialized) {
      await auth.initialize(client)
    }

    // authorised
    if (auth.account) {
      return next()
    }
    // unauthorised
    return next({path: '/app/login', query: {
      redirectPath: encodeURIComponent(to.fullPath)
    }})
  }

  // unguarded
  next()
})


export default router
