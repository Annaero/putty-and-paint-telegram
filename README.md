Use Vercel functions to collect new posts in [P&P](https://www.puttyandpaint.com/) projects.
For webhook calling uses cron-job.org

# Python
```shell
    pip install pipenv
    pipenv shell
    pipenv install
```

# Vercel
```shell
    npm i -g vercel
    vercel login
    vercel env pull .env.development.local
    vercel dev
```