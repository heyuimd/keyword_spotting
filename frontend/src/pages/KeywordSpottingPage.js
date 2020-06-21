import React, {useState, useCallback, useEffect, useRef} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Grid, Button} from '@material-ui/core';
import {
  WbIncandescentOutlined as LightBulbIcon,
} from '@material-ui/icons';

import {useDispatchContext} from "../components/ContextProvider";
import Greeting from "../components/Greeting";

const useStyles = makeStyles(() => ({
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


function KeywordSpottingPage() {
  const classes = useStyles();
  const [started, setStarted] = useState(false);
  const [connected, setConnected] = useState(false);
  const [keyword, setKeyword] = useState({
    detected: false,
    msg: '',
  });
  const dispatch = useDispatchContext();
  const wsRef = useRef(null);
  const audioCtxRef = useRef(null);
  const timer = useRef(null);

  useEffect(() => {
    const getMedia = async ws => {
      const stream = await navigator.mediaDevices
        .getUserMedia({
          video: false,
          audio: {
            sampleRate: 16000,
            channelCount: 1,
          },
        })
      const context = new AudioContext({sampleRate: 16000});
      const source = context.createMediaStreamSource(stream);
      const processor = context.createScriptProcessor(16384, 1, 1);

      source.connect(processor);
      processor.connect(context.destination);

      processor.onaudioprocess = e => {
        if (ws.readyState === 1) {
          ws.send(e.inputBuffer.getChannelData(0));
        }
      }

      audioCtxRef.current = context;
    };

    const closeAudioContext = async () => {
      if (audioCtxRef.current) {
        await audioCtxRef.current.close();
        audioCtxRef.current = null;
      }
    }

    if (connected && wsRef.current) {
      getMedia(wsRef.current);
    } else if (!connected && wsRef.current === null) {
      closeAudioContext();
    }
  }, [connected]);

  useEffect(() => {
    if (started && wsRef.current === null) {
      const ws = new WebSocket('ws://0.0.0.0:8080/ws/keyword-spotting');
      ws.onopen = e => {
        wsRef.current = ws;
        setConnected(true);
      }
      ws.onmessage = e => {
        const data = JSON.parse(e.data);
        if (timer.current) {
          clearTimeout(timer.current);
        }
        setKeyword({
          detected: true,
          msg: data['msg'],
        });
        timer.current = setTimeout(() => setKeyword({
          detected: false,
          msg: '',
        }), 2000);
      }
      ws.onclose = e => {
        wsRef.current = null;
        setConnected(false);
        setStarted(false);
        const randomInt = parseInt(Math.random() * 1000)
        dispatch({
          type: 'notify',
          payload: e.reason
            ? `${e.reason} [${randomInt}]`
            : `connection closed [${randomInt}]`,
        });
      }
    } else {
      if (wsRef.current) {
        const state = wsRef.current.readyState;
        if (state !== 2 && state !== 3) {
          wsRef.current.close();
        }
        wsRef.current = null;
      }
    }
  }, [started]);

  const handleClick = useCallback(() => {
    setStarted(state => !state);
  }, [setStarted]);

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
        {keyword.detected
          ? <LightBulbIcon
            className={classes.lightBulbOn}
          />
          : <LightBulbIcon
            className={classes.lightBulbOff}
          />
        }
      </Grid>
      <Grid item>
        <Greeting show={keyword.detected}>
          {keyword.detected ? keyword.msg : 'hidden'}
        </Greeting>
      </Grid>
      <Grid item>
        <Button
          variant='outlined'
          color='primary'
          onClick={handleClick}
        >
          {started
            ? 'Stop Listening'
            : 'Start Listening'}
        </Button>
      </Grid>
    </Grid>
  );
}

export default KeywordSpottingPage;
