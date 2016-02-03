var React = require('react');
var ReactIntl = require('react-intl');

var JarrTime = React.createClass({
    mixins: [ReactIntl.IntlMixin],
    propTypes: {stamp: React.PropTypes.number.isRequired,
                text: React.PropTypes.string.isRequired},
    render: function() {
        return (<time dateTime={this.props.text} title={this.props.text}>
                    {this.formatRelative(this.props.stamp)}
                </time>);
    },
});

module.exports = JarrTime;
