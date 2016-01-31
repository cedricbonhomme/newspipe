var React = require('react');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');
var Nav = require('react-bootstrap/lib/Nav');
var NavItem = require('react-bootstrap/lib/NavItem');
var Navbar = require('react-bootstrap/lib/Navbar');
var NavDropdown = require('react-bootstrap/lib/NavDropdown');
var MenuItem = require('react-bootstrap/lib/MenuItem');
var Button = require('react-bootstrap/lib/Button');
var Input = require('react-bootstrap/lib/Input');

var MenuStore = require('../stores/MenuStore');

JarrNavBar = React.createClass({
    getInitialState: function() {
        return {is_admin: MenuStore._datas.is_admin,
                crawling_method: MenuStore._datas.crawling_method};
    },
    buttonFetch: function() {
        if(this.state.is_admin && this.state.crawling_method != 'http') {
            return <NavItem eventKey={2} href="/fetch"><Glyphicon glyph="import" />Fetch</NavItem>;
        }
    },
    buttonAdmin: function() {
        if(this.state.is_admin) {
            return (<NavDropdown title={<Glyphicon glyph='cog' />}
                            id='admin-dropdown'>
                        <MenuItem href="/admin/dashboard">
                            <Glyphicon glyph="dashboard" />Dashboard
                        </MenuItem>
                    </NavDropdown>);
        }
    },
    render: function() {
        var gl_title = (<span>
                            <Glyphicon glyph="plus-sign" />Add a new feed
                        </span>);
        return (<Navbar fixedTop inverse className="navbar-custom">
                    <Navbar.Header>
                        <Navbar.Brand>
                            <a href="/">JARR</a>
                        </Navbar.Brand>
                        <Navbar.Toggle />
                    </Navbar.Header>
                    <Nav pullRight>
                        <Navbar.Form pullLeft>
                            <form action="/feed/bookmarklet" method="GET">
                            <Input name="url" type="text"
                                   placeholder="Add a new feed" />
                            <Button type="submit">Submit</Button>
                            </form>
                        </Navbar.Form>
                        {this.buttonFetch()}
                        <NavDropdown title="Feed" id="feed-mgmt-dropdown">
                            <MenuItem href="/feeds/inactives">Inactive</MenuItem>
                            <MenuItem href="/articles/history">History</MenuItem>
                            <MenuItem href="/feeds/">All</MenuItem>
                        </NavDropdown>
                        {this.buttonAdmin()}
                        <NavDropdown title={<Glyphicon glyph='user' />}
                                id="user-dropdown">
                            <MenuItem href="/user/profile">
                                <Glyphicon glyph="user" />Profile
                            </MenuItem>
                            <MenuItem href="/user/management">
                                <Glyphicon glyph="cog" />Your data
                            </MenuItem>
                            <MenuItem href="/about">
                                <Glyphicon glyph="question-sign" />About
                            </MenuItem>
                            <MenuItem href="/logout">
                                <Glyphicon glyph="log-out" />Logout
                            </MenuItem>
                        </NavDropdown>
                    </Nav>
                </Navbar>
        );
    },
    componentDidMount: function() {
        MenuStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MenuStore.getAll();
        this.setState({is_admin: datas.is_admin,
                       crawling_method: datas.crawling_method});
    },
});

module.exports = JarrNavBar;
