var React = require('react');

var JarrTime = React.createClass({
    propTypes: {stamp: React.PropTypes.string.isRequired,
                text: React.PropTypes.string.isRequired},
    render: function() {
        return (<time dateTime={this.props.text} title={this.props.text}>
                    {this.props.stamp}
                </time>);
    },
});

module.exports = JarrTime;
