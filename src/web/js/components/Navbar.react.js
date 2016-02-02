var React = require('react');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');
var Nav = require('react-bootstrap/lib/Nav');
var NavItem = require('react-bootstrap/lib/NavItem');
var Navbar = require('react-bootstrap/lib/Navbar');
var NavDropdown = require('react-bootstrap/lib/NavDropdown');
var MenuItem = require('react-bootstrap/lib/MenuItem');
var Modal = require('react-bootstrap/lib/Modal');
var Button = require('react-bootstrap/lib/Button');
var Input = require('react-bootstrap/lib/Input');

var MenuStore = require('../stores/MenuStore');

JarrNavBar = React.createClass({
    getInitialState: function() {
        return {is_admin: MenuStore._datas.is_admin,
                crawling_method: MenuStore._datas.crawling_method,
                showModal: false, modalType: null};
    },
    buttonFetch: function() {
        if(this.state.is_admin && this.state.crawling_method != 'http') {
            return (<NavItem eventKey={2} href="/fetch">
                        <Glyphicon glyph="import" />Fetch
                    </NavItem>);
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
    getModal: function() {
        var heading = null;
        var action = null;
        var body = null;
        if(this.state.modalType == 'addFeed') {
            heading = 'Add a new feed';
            action = '/feed/bookmarklet';
            placeholder = "Site or feed url, we'll sort it out later ;)";
            body = <Input name="url" type="text" placeholder={placeholder} />;
        } else {
            heading = 'Add a new category';
            action = '/category/create';
            body = <Input name="name" type="text"
                          placeholder="Name, there isn't much more to it" />;
        }
        return (<Modal show={this.state.showModal} onHide={this.close}>
                  <form action={action} method="POST">
                    <Modal.Header closeButton>
                      <Modal.Title>{heading}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                      {body}
                    </Modal.Body>
                    <Modal.Footer>
                      <Button type="submit">Add</Button>
                    </Modal.Footer>
                  </form>
                </Modal>);
    },
    close: function() {
        this.setState({showModal: false, modalType: null});
    },
    openAddFeed: function() {
        this.setState({showModal: true, modalType: 'addFeed'});
    },
    openAddCategory: function() {
        this.setState({showModal: true, modalType: 'addCategory'});
    },
    render: function() {
        return (<Navbar fixedTop inverse id="jarrnav">
                    {this.getModal()}
                    <Navbar.Header>
                        <Navbar.Brand>
                            <a href="/">JARR</a>
                        </Navbar.Brand>
                        <Navbar.Toggle />
                    </Navbar.Header>
                    <Nav pullRight>
                        {this.buttonFetch()}
                        <NavItem className="jarrnavitem"
                                 onClick={this.openAddFeed} href="#">
                            <Glyphicon glyph="plus-sign" />Add a new feed
                        </NavItem>
                        <NavItem className="jarrnavitem"
                                 onClick={this.openAddCategory} href="#">
                            <Glyphicon glyph="plus-sign" />Add a new category
                        </NavItem>
                        <NavDropdown title="Feed" id="feed-dropdown">
                            <MenuItem href="/feeds/inactives">
                                Inactives
                            </MenuItem>
                            <MenuItem href="/articles/history">
                                History
                            </MenuItem>
                            <MenuItem href="/feeds/">
                                All
                            </MenuItem>
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
