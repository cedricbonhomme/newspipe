var React = require('react');

var RightPanelStore = require('../stores/RightPanelStore');
var RightPanelActions = require('../actions/RightPanelActions');


var Article = React.createClass({

    render: function() {
        return (<div />);
    },
});


var Feed = React.createClass({
    render: function() {
        return (<div />);
    },
});


var Category = React.createClass({
    render: function() {
        return (<div />);
    },
});


var RightPanelMenu = React.createClass({
    getInitialState: function() {
        return {};
    },
    render: function() {
        return (<div />);
    },
    componentDidMount: function() {
        RightPanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        RightPanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
    },
});

var RightPanel = React.createClass({
    getInitialState: function() {
        return {obj_type: null, obj_id: null};
    },
    render: function() {
        if (this.state.obj_type == 'article') {
            return <Article />;
        } else if (this.state.obj_type == 'feed') {
            return <Feed />;
        } else if (this.state.obj_type == 'category') {
            return <Category />;
        }
        return <div />;
    },
    componentDidMount: function() {
        RightPanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        RightPanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
    },
});

module.exports = {RightPanelMenu: RightPanelMenu, RightPanel: RightPanel};
