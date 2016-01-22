var React = require('react');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');

var MenuStore = require('../stores/MenuStore');
var MenuActions = require('../actions/MenuActions');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var FeedItem = React.createClass({
    propTypes: {feed_id: React.PropTypes.number.isRequired,
                title: React.PropTypes.string.isRequired,
                unread: React.PropTypes.number.isRequired,
                icon_url: React.PropTypes.string,
    },
    getInitialState: function() {
        return {feed_id: this.props.feed_id,
                title: this.props.title,
                unread: this.props.unread,
                icon_url: this.props.icon_url,
        };
    },
    render: function() {
        var unread = undefined;
        var icon = undefined;
        if(this.state.icon_url){
            icon = (<img width="16px" src={this.state.icon_url} />);
        } else {
            icon = (<span className="glyphicon glyphicon-ban-circle" />);
        }
        if(this.state.unread){
            unread = (
                    <span className="badge pull-right">
                        {this.state.unread}
                    </span>
            );
        }
        return (<li onMouseDown={this.handleClick}>
                    {icon} {this.state.title} {unread}
                </li>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setFeedFilter(this.state.feed_id);
    },
});

var Category = React.createClass({
    propTypes: {category_id: React.PropTypes.number.isRequired,
                name: React.PropTypes.string.isRequired,
                feeds: React.PropTypes.array.isRequired,
                unread: React.PropTypes.number.isRequired,
    },
    getInitialState: function() {
        return {category_id: this.props.category_id,
                name: this.props.name,
                feeds: this.props.feeds,
                unread: this.props.unread,
        };
    },
    render: function() {
        unread = undefined;
        if(this.state.unread){
            unread = (
                    <span className="badge pull-right">
                        {this.state.unread}
                    </span>
            );
        }
        return (<div>
                    <h3 onMouseDown={this.handleClick}>
                        {this.state.name} {unread}
                    </h3>
                    <ul className="nav nav-sidebar">
                    {this.state.feeds.map(function(feed){
                     return <FeedItem key={"feed" + feed.id}
                                      feed_id={feed.id}
                                      title={feed.title}
                                      unread={feed.unread}
                                      icon_url={feed.icon_url} />;})}
                    </ul>
                </div>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setCategoryFilter(this.state.category_id);
    },
});

var Menu = React.createClass({
    getInitialState: function() {
        return {filter: 'all', categories: [], all_unread_count: 0};
    },
    render: function() {
        return (<div id="sidebar" data-spy="affix" role="navigation"
                     className="col-md-2 sidebar sidebar-offcanvas pre-scrollable hidden-sm hidden-xs affix">
                    <ButtonGroup>
                        <Button active={this.state.filter == "all"}
                                onMouseDown={MenuActions.setFilterMenuAll}
                                bsSize="small">All</Button>
                        <Button active={this.state.filter == "unread"}
                                onMouseDown={MenuActions.setFilterMenuUnread}
                                bsSize="small">Unread</Button>
                        <Button active={this.state.filter == "error"}
                                onMouseDown={MenuActions.setFilterMenuError}
                                bsSize="small" bsStyle="warning">Error</Button>
                    </ButtonGroup>
                    {this.state.categories.map(function(category){
                        return (<Category key={"cat" + category.id}
                                          category_id={category.id}
                                          feeds={category.feeds}
                                          name={category.name}
                                          unread={category.unread} />);
                        })}

                </div>
        );
    },
    componentDidMount: function() {
        MenuActions.reload();
        MenuStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MenuStore.getAll();
        this.setState({filter: datas.filter,
                       categories: datas.categories,
                       all_unread_count: datas.all_unread_count});
    },
});

module.exports = Menu;
