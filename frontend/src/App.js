import React, { useState, useCallback, useEffect, } from 'react';
import styled from "styled-components";
import {makeStyles} from '@material-ui/core/styles';
import { Grid, Button } from '@material-ui/core';
import {
  WbIncandescentOutlined as LightBulbIcon,
} from '@material-ui/icons';

const useStyles = makeStyles(theme => ({
  root: {
    minHeight: '100vh',
    overflow: 'auto',
  },
  lightBulbOn: {
    color: 'red',
    fontSize: 200,
  },
  lightBulbOff: {
    color: 'gray',
    fontSize: 200,
  },
}));

const Greeting = styled.h1`
  font-size: 1.5em;
  text-align: center;
  color: pink;
  visibility: ${props => props.show ? 'visible' : 'hidden'};
`;


function App() {
  const classes = useStyles();
  const [start, setStart] = useState(false);

  //useEffect(() => {
  //  const getMedia = async () => {
  //    const stream = await navigator.mediaDevices
  //      .getUserMedia({audio: true, video: false})

  //    const context = new AudioContext();
  //    const source = context.createMediaStreamSource(stream);
  //    const processor = context.createScriptProcessor(1024, 1, 1);

  //    source.connect(processor);
  //    processor.connect(context.destination);

  //    processor.onaudioprocess = function (e) {
  //      console.log(e.inputBuffer);
  //    }
  //  };

  //  getMedia();
  //}, []);

  useEffect(() => {
    const ws = new WebSocket( 'ws://0.0.0.0:8080/ws/keyword-spotting');
    ws.onerror = e => {
      console.log(e);
    }
    ws.onclose = e => {
      console.log(e);
    }
  }, []);

  const handleClick = useCallback(() => {
    setStart((state) => !state);
  }, [setStart]);

  return (
    <Grid
      className={classes.root}
      spacing={3}
      container
      direction='column'
      justify='center'
      alignItems='center'
    >
      <Grid item>
        {start
          ? <LightBulbIcon
            className={classes.lightBulbOn}
          />
          : <LightBulbIcon
            className={classes.lightBulbOff}
          />
        }
      </Grid>
      <Grid item>
        <Greeting show={start}>
          HELLO
        </Greeting>
      </Grid>
      <Grid item>
        <Button
          variant='outlined'
          color='primary'
          onClick={handleClick}
        >
          Start Listening
        </Button>
      </Grid>
    </Grid>
  );
}

export default App;
