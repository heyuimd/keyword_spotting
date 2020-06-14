import React from 'react';
import KeywordSpottingPage from "./pages/KeywordSpottingPage";
import ContextProvider from "./components/ContextProvider";
import MessageSnackBar from "./components/MessageSnackBar";

const initialState = {
  notification: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'notify':
      return {...state, notification: action.payload};
    default:
      throw new Error();
  }
}

function App() {
  return (
    <>
      <ContextProvider
        initialState={initialState}
        reducer={reducer}
      >
        <KeywordSpottingPage/>
        <MessageSnackBar/>
      </ContextProvider>
    </>
  );
}

export default App;
