var React = require('react');
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
        return {article_id: this.props.article_id,
                title: this.props.title,
                icon_url: this.props.icon_url,
                feed_title: this.props.feed_title,
                date: this.props.date,
                read: this.props.read,
                liked: this.props.liked,
        };
    },
    render: function() {
        var read = this.state.read ? 'r' : '';
        var liked = this.state.liked ? 'l' : '';
        var icon = undefined;
        if(this.state.icon_url){
            icon = (<img width="16px" src={this.state.icon_url} />);
        } else {
            icon = (<span className="glyphicon glyphicon-ban-circle" />);
        }
        return (
                <tr>
                <td>{icon}{liked}</td>
                <td>
                    <a href={'/redirect/' + this.state.article_id}>
                        {this.state.feed_title}
                    </a>
                </td>
                <td>
                    <a href={'/article/' + this.state.article_id}>
                        {this.state.title}
                    </a>
                </td>
                <td>{this.state.date}</td>
                </tr>
        );
    },
});

var TableBody = React.createClass({
    propTypes: {articles: React.PropTypes.array.isRequired,
    },
    getInitialState: function() {
        return {articles: this.props.articles,
        };
    },
    render: function() {
        return (<div className="table-responsive">
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
    }
});

var MiddlePanel = React.createClass({
    getInitialState: function() {
        return {articles: []};
    },
    render: function() {
        var body = null;
        if(this.state.articles.length) {
            body = (<TableBody articles={this.state.articles} />);
        }
        return (<div className="col-md-offset-2 col-md-10 main">{body}</div>);
    },
    componentDidMount: function() {
        MiddlePanelActions.reload();
        MiddlePanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MiddlePanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MiddlePanelStore.getAll();
        this.setState({articles: datas.articles});
    },
});

module.exports = MiddlePanel;
