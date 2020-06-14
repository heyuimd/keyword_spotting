import React, {createContext, useContext, useReducer} from 'react';

const DispatchContext = createContext();
const StateContext = createContext();

function ContextProvider({reducer, initialState, children}) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <DispatchContext.Provider value={dispatch}>
      <StateContext.Provider value={state}>
        {children}
      </StateContext.Provider>
    </DispatchContext.Provider>
  );
}

export const useDispatchContext = () => useContext(DispatchContext);
export const useStateContext = () => useContext(StateContext);

export default ContextProvider;
