var React = require('react');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');

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
        var read = this.state.read ? 'r' : '';
        var liked = this.state.liked ? 'l' : '';
        var icon = undefined;
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = (<span className="glyphicon glyphicon-ban-circle" />);
        }
        return (
                <tr>
                <td>{icon}{liked}</td>
                <td>
                    <a href={'/redirect/' + this.props.article_id}>
                        {this.props.feed_title}
                    </a>
                </td>
                <td>
                    <a href={'/article/' + this.props.article_id}>
                        {this.props.title}
                    </a>
                </td>
                <td>{this.props.date}</td>
                </tr>
        );
    },
});

var TableBody = React.createClass({
    getInitialState: function() {
        return {filter: 'unread', articles: []};
    },
    render: function() {
        return (<div className="table-responsive">
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
                <table className="table table-striped strict-table">
                <tbody>
                    {this.state.articles.map(function(article){
                     return (<TableLine key={"article" + article.article_id}
                                        title={article.title}
                                        icon_url={article.icon_url}
                                        read={article.read}
                                        liked={article.liked}
                                        date={article.date}
                                        article_id={article.article_id}
                                        feed_title={article.feed_title} />);})}
                </tbody>
                </table>
                </div>
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

var MiddlePanel = React.createClass({
    render: function() {
        return (<div className="col-md-offset-2 col-md-10 main">
                    <TableBody />
                </div>
        );
    },
});

module.exports = MiddlePanel;
