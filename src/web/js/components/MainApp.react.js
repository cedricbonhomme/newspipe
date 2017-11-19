var React = require('react');
var createReactClass = require('create-react-class');
var Col = require('react-bootstrap/lib/Col');
var Grid = require('react-bootstrap/lib/Grid');
var PropTypes = require('prop-types');

var Menu = require('./Menu.react');
var MiddlePanel = require('./MiddlePanel.react');
var RightPanel = require('./RightPanel.react');


var MainApp = createReactClass({
    render: function() {
        return (<div>
                    <Grid fluid id="newspipe-container">
                        <Menu />
                        <Col id="middle-panel" mdOffset={3} lgOffset={2}
                                            xs={12} sm={4} md={4} lg={4}>
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
