import './index.css';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import {CssBaseline} from '@material-ui/core';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(
  <React.StrictMode>
    <CssBaseline/>
    <App/>
  </React.StrictMode>,
  document.getElementById('root')
);

serviceWorker.unregister();
