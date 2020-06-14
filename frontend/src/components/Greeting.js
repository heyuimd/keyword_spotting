import React from 'react';
import styled from "styled-components";

const Greeting = styled.h1`
  font-size: 1.5em;
  text-align: center;
  color: pink;
  visibility: ${props => props.show ? 'visible' : 'hidden'};
`;

export default Greeting;
