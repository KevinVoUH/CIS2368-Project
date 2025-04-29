const express = require('express');
const app = express();
const path = require('path');
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const API_BASE = 'http://localhost:5000/api';

app.get('/', (req, res) => {
    res.render('home');
});

// Books
app.get('/books', async (req, res) => {
    try {
        const response = await fetch(API_BASE + '/books');
        if (!response.ok) throw new Error('API error on /books');
        let books = await response.json();
        if (!books) books = [];
        res.render('books', { books });
    } catch (err) {
        console.error(err);
        res.render('books', { books: [] });
    }
});

// Customers
app.get('/customers', async (req, res) => {
    try {
        const response = await fetch(API_BASE + '/customers');
        if (!response.ok) throw new Error('API error on /customers');
        let customers = await response.json();
        if (!customers) customers = [];
        res.render('customers', { customers });
    } catch (err) {
        console.error(err);
        res.render('customers', { customers: [] });
    }
});

// Borrowings
app.get('/borrowings', async (req, res) => {
    try {
        const borrowsResponse = await fetch(API_BASE + '/borrowings');
        if (!borrowsResponse.ok) throw new Error('API error on /borrowings');
        let borrows = await borrowsResponse.json();
        if (!borrows) borrows = [];

        const booksResponse = await fetch(API_BASE + '/books');
        if (!booksResponse.ok) throw new Error('API error on books fetch inside /borrowings');
        let books = await booksResponse.json();
        if (!books) books = [];

        const customersResponse = await fetch(API_BASE + '/customers');
        if (!customersResponse.ok) throw new Error('API error on customers fetch inside /borrowings');
        let customers = await customersResponse.json();
        if (!customers) customers = [];

        res.render('borrowings', { borrows, books, customers });
    } catch (err) {
        console.error(err);
        res.render('borrowings', { borrows: [], books: [], customers: [] });
    }
});

app.listen(3000, () => console.log('Frontend server started on port 3000'));
