jQuery(document).ready(function($) {
    var id = 1;
    function python(terminal) {
        function ajax_error(xhr, status) {
            terminal.resume();
            terminal.error('&#91;AJAX&#93; ' + status + ' server response\n' +
                           xhr.responseText);
            terminal.pop();
        }
        function json_error(error) {
            if (typeof error == 'string') {
                terminal.error(error);
            } else {
                if (error.message) {
                    terminal.echo(error.message);
                }
                if (error.error.traceback) {
                    terminal.echo(error.error.traceback);
                }
            }
        }
        var url = 'http://localhost:6969/';
        //url = 'rpc.cgi';
        function rpc_py(method, params, echo) {
            if (params === undefined) {
                params = [];
            }
            terminal.pause();
            $.jrpc(url, id++, method, params, function(data) {
                terminal.resume();
                if (data.error) {
                    json_error(data.error);
                } else if (data.result) {
                    if (echo === undefined || echo) {
                        terminal.echo(data.result);
                    }
                }
            }, ajax_error);
        }

        terminal.pause();
        var session_id = 'test';
        $.jrpc(url, id++, 'start', [], function(data) {
            terminal.resume();
            if (data.error) {
              json_error(data.error);
            }
            else if (data.result) {
              session_id = data.result;
              rpc_py('info', [])
            }
        }, ajax_error);
        return {
          info: function() {
            rpc_py('info', []);
          },

          use: function(version) {
            rpc_py('use', [session_id, version]);
          },

          evaluate: function(code) {
            rpc_py('evaluate', [session_id, code]);
          },

          destroy: function() {
            rpc_py('destroy', [session_id]);
          }
        };
    }

    var py; // python rpc
    var python_code = '';
    $('#terminal').terminal(function(command, term) {
        if (command.match(/^help$/)) {
          if (command.match(/^help */)) {
            term.echo("Type help() for interactive help, or " +
                      "help(object) for help about object.");
          }
          else {
            var rgx = /help\((.*)\)/;
              py.evaluate(command.replace(rgx, 'print $1.__doc__'));
          }
        }
        else if (command.match(/^info$/)) {
          py.info('info');
        }
        else if (matches = command.match(/^use (.+?)$/)) {
          var version = matches[1];
          py.use(version);
        }
        else if (command.match(/: *$/)) {
            python_code += command + "\n";
            term.set_prompt('...');
        } else if (python_code) {
            if (command == '') {
                term.set_prompt('>>>');
                py.evaluate(python_code);
                python_code = '';
            } else {
                python_code += command + "\n";
                }
        } else {
            py.evaluate(command);
        }
    }, {
      prompt: '>>>',
      name: 'python',
      greetings: null,
      onInit: function(terminal) {
          py = python(terminal);
      },

      width: 800,
      height: 355
    });

    $(window).unload(function() {
        py.destroy();
    });
});
