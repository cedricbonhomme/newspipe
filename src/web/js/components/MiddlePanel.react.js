var React = require('react');
var Row = require('react-bootstrap/Row');
var Button = require('react-bootstrap/Button');
var ButtonGroup = require('react-bootstrap/ButtonGroup');
var Glyphicon = require('react-bootstrap/Glyphicon');

var MiddlePanelStore = require('../stores/MiddlePanelStore');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var TableLine = React.createClass({
    propTypes: {article_id: React.PropTypes.number.isRequired,
                feed_title: React.PropTypes.string.isRequired,
                icon_url: React.PropTypes.string,
                title: React.PropTypes.string.isRequired,
                date: React.PropTypes.string.isRequired,
                read: React.PropTypes.bool.isRequired,
                liked: React.PropTypes.bool.isRequired,
    },
    getInitialState: function() {
        return {read: this.props.read, liked: this.props.liked};
    },
    render: function() {
        var liked = this.state.liked ? 'l' : '';
        var icon = null;
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = <Glyphicon glyph="ban-circle" />;
        }
        var title = (<a href={'/article/redirect/' + this.props.article_id}>
                        {icon} {this.props.feed_title}
                     </a>);
        var read = (<Glyphicon glyph={this.state.read?"check":"unchecked"}
                               onClick={this.toogleRead} />);
        var liked = (<Glyphicon glyph={this.state.liked?"star":"star-empty"}
                                onClick={this.toogleLike} />);
        return (<div className="list-group-item">
                    <h4>{title}</h4>
                    {read} {liked} {this.props.title}
                </div>
        );
    },
    toogleRead: function() {
        this.setState({read: !this.state.read});
        MiddlePanelActions.changeRead(this.props.category_id,
                this.props.feed_id, this.props.article_id, !this.state.read);
    },
    toogleLike: function() {
        this.setState({liked: !this.state.liked});
        MiddlePanelActions.changeLike(this.props.category_id,
                this.props.feed_id, this.props.article_id, !this.state.liked);
    },
});

var MiddlePanelFilter = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore._datas.filter};
    },
    render: function() {
        return (<Row className="show-grid">
                    <ButtonGroup>
                        <Button active={this.state.filter == "all"}
                                onMouseDown={() => this.setFilter("all")}
                                bsSize="small">All</Button>
                        <Button active={this.state.filter == "unread"}
                                onMouseDown={() => this.setFilter("unread")}
                                bsSize="small">Unread</Button>
                        <Button active={this.state.filter == "liked"}
                                onMouseDown={() => this.setFilter("liked")}
                                bsSize="small">Liked</Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onMouseDown={MiddlePanelActions.markAllAsRead}
                                bsSize="small">Mark all as read</Button>
                    </ButtonGroup>
                </Row>
        );
    },
    setFilter: function(filter) {
        this.setState({filter: filter});
        MiddlePanelActions.setFilter(filter);
    }
});

var MiddlePanel = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore._datas.filter, articles: []};
    },
    render: function() {
        return (<Row className="show-grid">
                    <div className="list-group">
                    {this.state.articles.map(function(article){
                        return (<TableLine key={"a" + article.article_id}
                                        title={article.title}
                                        icon_url={article.icon_url}
                                        read={article.read}
                                        liked={article.liked}
                                        date={article.date}
                                        article_id={article.article_id}
                                        feed_id={article.feed_id}
                                        category_id={article.category_id}
                                        feed_title={article.feed_title} />);})}
                    </div>
                </Row>
        );
    },
    componentDidMount: function() {
        MiddlePanelActions.reload();
        MiddlePanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MiddlePanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState({filter: MiddlePanelStore._datas.filter,
                       articles: MiddlePanelStore.getArticles()});
    },
});

module.exports = {MiddlePanel: MiddlePanel,
                  MiddlePanelFilter: MiddlePanelFilter};
