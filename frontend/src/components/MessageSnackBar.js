import React, {useState, useEffect, useCallback} from 'react';
import clsx from 'clsx';
import {IconButton, Snackbar, SnackbarContent} from '@material-ui/core';
import {makeStyles} from '@material-ui/core/styles';
import {
  Error as ErrorIcon,
  Close as CloseIcon,
} from '@material-ui/icons';
import {useStateContext} from './ContextProvider';

const useStyles = makeStyles(theme => ({
  contents: {
    backgroundColor: theme.palette.error.dark,
  },
  icon: {
    fontSize: 20,
  },
  iconVariant: {
    opacity: 0.9,
    marginRight: theme.spacing(1),
  },
  message: {
    display: 'flex',
    alignItems: 'center',
  },
}));

function MessageSnackBar() {
  const classes = useStyles();
  const [open, setOpen] = useState(false);
  const {notification} = useStateContext();

  useEffect(() => {
    if (notification) {
      setOpen(true);
    } else {
      setOpen(false);
    }
  }, [notification]);

  const handleClose = useCallback((event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
  }, [setOpen]);

  return (
    <Snackbar
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'center',
      }}
      open={open}
      autoHideDuration={3000}
      onClose={handleClose}
    >
      <SnackbarContent
        className={classes.contents}
        message={
          <span className={classes.message}>
            <ErrorIcon
              className={clsx(classes.icon, classes.iconVariant)}
            />
            {notification}
          </span>
        }
        action={[
          <IconButton
            key="close"
            color="inherit"
            onClick={handleClose}
          >
            <CloseIcon className={classes.icon}/>
          </IconButton>,
        ]}
      />
    </Snackbar>
  );
}

export default MessageSnackBar;
