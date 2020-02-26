var React = require('react');
var createReactClass = require('create-react-class');
var PropTypes = require('prop-types');

var JarrTime = createReactClass({
    propTypes: {stamp: PropTypes.string.isRequired,
                text: PropTypes.string.isRequired},
    render: function() {
        return (<time dateTime={this.props.text} title={this.props.text}>
                    {this.props.stamp}
                </time>);
    },
});

module.exports = JarrTime;
