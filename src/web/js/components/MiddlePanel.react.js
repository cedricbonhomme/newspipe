var React = require('react');
var Row = require('react-bootstrap/lib/Row');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var ListGroup = require('react-bootstrap/lib/ListGroup');
var ListGroupItem = require('react-bootstrap/lib/ListGroupItem');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');

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
        var title = (<a href={'/redirect/' + this.props.article_id}>
                        {icon} {this.props.feed_title}
                     </a>);
        var read = (<Glyphicon glyph={this.state.read?"check":"unchecked"}
                               onClick={this.toogleRead} />);
        var liked = (<Glyphicon glyph={this.state.liked?"star":"star-empty"}
                                onClick={this.toogleLike} />);
        return (
                <ListGroupItem header={title}>
                            {read}
                            {liked}
                    {this.props.title}
                </ListGroupItem>
        );
    },
    toogleRead: function() {
        this.setState({read: !this.state.read});
        MiddlePanelActions.changeRead(this.props.article_id, !this.state.read);
    },
    toogleLike: function() {
        this.setState({liked: !this.state.liked});
        MiddlePanelActions.changeLike(this.props.article_id, !this.state.liked);
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
                                onMouseDown={MiddlePanelActions.setFilterAll}
                                bsSize="small">All</Button>
                        <Button active={this.state.filter == "unread"}
                                onMouseDown={MiddlePanelActions.setFilterUnread}
                                bsSize="small">Unread</Button>
                        <Button active={this.state.filter == "liked"}
                                onMouseDown={MiddlePanelActions.setFilterLiked}
                                bsSize="small">Liked</Button>
                    </ButtonGroup>
                </Row>
        );
    },
    componentDidMount: function() {
        MiddlePanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MiddlePanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState({filter: MiddlePanelStore._datas.filter});
    },
});

var MiddlePanel = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore._datas.filter, articles: []};
    },
    render: function() {
        return (<Row className="show-grid">
                    <ListGroup>
                    {this.state.articles.map(function(article){
                        return (<TableLine key={"a" + article.article_id}
                                        title={article.title}
                                        icon_url={article.icon_url}
                                        read={article.read}
                                        liked={article.liked}
                                        date={article.date}
                                        article_id={article.article_id}
                                        feed_title={article.feed_title} />);})}
                    </ListGroup>
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
