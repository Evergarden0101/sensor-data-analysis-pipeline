import express from 'express';

const app = express();
app.use(express.json());

const port = 8000;

app.get('/hello', (req, res) => {
    res.json("Hello world!");
});


app.listen(port, () => {
    console.log('Server is listening on port 8000')
})