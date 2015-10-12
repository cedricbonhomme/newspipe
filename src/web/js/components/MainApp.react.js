var Menu = require('./Menu.react');
var MiddlePanel = require('./MiddlePanel.react');
var React = require('react');


var MainApp = React.createClass({
    render: function() {
        return (<div className="container-fluid">
                    <div className="row row-offcanvas row-offcanvas-left">
                        <Menu />
                        <MiddlePanel />
                    </div>
                </div>
       );
    },
});

module.exports = MainApp;
