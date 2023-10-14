import type { Configuration } from '@azure/msal-browser'
import { LogLevel } from '@azure/msal-browser'

export const scopes = [
  'openid','profile'
]

export const config: Configuration = {
  // required
  auth: {
    // must match info in dashboard
    clientId: "84f6c12a-12bf-4fd0-91bc-2dfb30ecadea",
    authority: 'https://login.microsoftonline.com/4ea43e8a-132e-48c0-901d-52dd22e7cdf3',
    knownAuthorities: [
      'https://login.microsoftonline.com/4ea43e8a-132e-48c0-901d-52dd22e7cdf3',
    ],

    // login redirect; must match path in dashboard
    redirectUri: `${window.location.origin}/callback.html`,
  },

  // optional
  system: {
    loggerOptions: {
      logLevel: LogLevel.Error,
      loggerCallback,
    }
  }
}
console.log(config)
function loggerCallback (level: LogLevel, message: string, containsPii: boolean) {
  if (!containsPii) {
    const parts = message.split(' : ')
    const text = parts.pop()
    switch (level) {
      case LogLevel.Error:
        return console.error(text)

      case LogLevel.Warning:
        return console.warn(text)

      case LogLevel.Info:
        return console.info(text)

      case LogLevel.Verbose:
        return console.debug(text)
    }
  }
}
