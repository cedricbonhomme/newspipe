var React = require('react');
var Col = require('react-bootstrap/lib/Col');
var Grid = require('react-bootstrap/lib/Grid');

var JarrNavBar = require('./Navbar.react');
var Menu = require('./Menu.react');
var MiddlePanel = require('./MiddlePanel.react');
var RightPanel = require('./RightPanel.react');


var MainApp = React.createClass({
    render: function() {
        return (<div>
                    <JarrNavBar />
                    <Grid fluid id="jarr-container">
                        <Menu />
                        <Col id="middle-panel" mdOffset={3} lgOffset={2}
                                            xs={4} sm={4} md={4} lg={4}>
                            <MiddlePanel.MiddlePanelFilter />
                            <MiddlePanel.MiddlePanel />
                        </Col>
                        <RightPanel />
                    </Grid>
                </div>
       );
    },
});

module.exports = MainApp;
