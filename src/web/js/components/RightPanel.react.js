var React = require('react');
var Col = require('react-bootstrap/Col');
var Panel = require('react-bootstrap/Panel');
var RightPanelStore = require('../stores/RightPanelStore');
var RightPanelActions = require('../actions/RightPanelActions');

var Article = React.createClass({
    propTypes: {article: React.PropTypes.object.isRequired},
    render: function() {
        return (<div />);
    },
});

var Feed = React.createClass({
    propTypes: {feed: React.PropTypes.object.isRequired},
    render: function() {
        var icon = null;
        if(this.props.feed.icon_url){
            icon = (<img width="16px" src={this.props.feed.icon_url} />);
        }
        var header = (<h4>
                        {icon}<strong>Title:</strong> {this.props.feed.title}
                      </h4>);
        return (<Panel header={header}>
                    <dl className="dl-horizontal">
                        <dt>Description</dt>
                        <dd>{this.props.feed.description}</dd>
                        <dt>Created on</dt>
                        <dd>{this.props.feed.created_date}</dd>
                        <dt>Feed adress</dt>
                        <dd>
                            <a href={this.props.feed.link}>
                                {this.props.feed.link}
                            </a>
                        </dd>
                        <dt>Site link</dt>
                        <dd>
                            <a href={this.props.feed.site_link}>
                                {this.props.feed.site_link}
                            </a>
                        </dd>
                        <dt>Last fetched</dt>
                        <dd>{this.props.feed.last_retrieved}</dd>
                        <dt>Enabled</dt>
                        <dd>{this.props.feed.enabled}</dd>
                    </dl>
                </Panel>
        );
    },
});

var Category = React.createClass({
    propTypes: {category: React.PropTypes.object.isRequired},
    render: function() {
        return (<Panel header={this.props.category.name}>
                test
                </Panel>
        );
    },
});

var RightPanel = React.createClass({
    getInitialState: function() {
        return {category: null, feed: null, article: null};
    },
    getCategoryCrum: function() {
        return (<li><a onClick={this.selectCategory} href="#">
                    {this.state.category.name}
                </a></li>);
    },
    getFeedCrum: function() {
        return (<li><a onClick={this.selectFeed} href="#">
                    {this.state.feed.title}
                </a></li>);
    },
    getArticleCrum: function() {
        return <li>Article</li>;
    },
    render: function() {
        var content = null;
        var breadcrum = null;
        if(this.state.article) {
            var breadcrum = (<ol className="breadcrumb">
                                {this.getCategoryCrum()}
                                {this.getFeedCrum()}
                                {this.getArticleCrum()}
                             </ol>);
            var content = <Article />;
        } else if(this.state.feed) {
            var breadcrum = (<ol className="breadcrumb">
                                {this.getCategoryCrum()}
                                {this.getFeedCrum()}
                             </ol>);
            var content = <Feed feed={this.state.feed} />;
        } else if(this.state.category) {
            var breadcrum = (<ol className="breadcrumb">
                                {this.getCategoryCrum()}
                             </ol>);
            var content = <Category category={this.state.category} />;
        }

        return (<Col id="right-panel" xsOffset={2} smOffset={2}
                                      mdOffset={7} lgOffset={6}
                                      xs={10} sm={10} md={5} lg={6}>
                    {breadcrum}
                    {content}
                </Col>
        );
    },
    selectCategory: function() {
        this.setState({feed: null, article: null});
    },
    selectFeed: function() {
        this.setState({article: null});
    },
    componentDidMount: function() {
        RightPanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        RightPanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState(RightPanelStore._datas);
    },
});

module.exports = RightPanel;
