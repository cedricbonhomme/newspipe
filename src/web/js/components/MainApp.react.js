var React = require('react');
var Col = require('react-bootstrap/Col');
var Row = require('react-bootstrap/Row');

var Menu = require('./Menu.react');
var MiddlePanel = require('./MiddlePanel.react');
var RightPanel = require('./RightPanel.react');


var MainApp = React.createClass({
    render: function() {
        return (<Row>
                    <Menu />
                    <Col xs={2} sm={2} md={4} lg={4}>
                        <MiddlePanel.MiddlePanelFilter />
                        <MiddlePanel.MiddlePanel />
                    </Col>
                    <Col xs={10} sm={10} md={8} lg={8}>
                        <RightPanel.RightPanelMenu />
                        <RightPanel.RightPanel />
                    </Col>
                </Row>
       );
    },
});

module.exports = MainApp;
