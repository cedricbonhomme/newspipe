var React = require('react');
var Col = require('react-bootstrap/Col');
var Grid = require('react-bootstrap/Grid');

var Menu = require('./Menu.react');
var MiddlePanel = require('./MiddlePanel.react');
var RightPanel = require('./RightPanel.react');


var MainApp = React.createClass({
    render: function() {
        return (<Grid fluid id="jarr-container">
                    <Menu />
                    <Col id="middle-panel" mdOffset={3} lgOffset={2}
                                           xs={2} sm={2} md={4} lg={4}>
                        <MiddlePanel.MiddlePanelFilter />
                        <MiddlePanel.MiddlePanel />
                    </Col>
                    <RightPanel />
                </Grid>
       );
    },
});

module.exports = MainApp;
