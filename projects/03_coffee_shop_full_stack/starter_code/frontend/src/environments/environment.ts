export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'fsnd-coffeeshop', // the auth0 domain prefix
    audience: 'Coffee', // the audience set for the auth0 app
    clientId: 'Rt5U5ELQnj9UiVvDsHzvLSF32udYDoC8', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application.
  }
};
// https://fsnd-coffeeshop.auth0.com/authorize?audience=Coffee&response_type=token
// &client_id=Rt5U5ELQnj9UiVvDsHzvLSF32udYDoC8&redirect_uri=http://localhost:8100/tabs/user-page

