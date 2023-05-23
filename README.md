# 401k_optimize

## Overview of Project
There are enough statistics available through the media to terify just about anyone into investing towards their retirement. And for a long time, one of the primary vehicles for every day working Americans is the 401k. The goal of this project is to provide a little bit of education, a slight bit of objectivity, and hopefully a useful tool to optimize your 401k contributions as you save for retirement.

### Purpose of Project
You just got a new job; congratulations! And even better, your new employer offers you the opportunity to invest in a 401k. Awesome. Maybe you get to sign up day one, or perhaps you have to wait a month. Whatever the case is, you log in to your shiny new 401k provider. And they start asking you questions. And not just one or two easy to answer questions, but things like, "How do you want to diversity your portfolio?". My who what? Rather quickly you have discovered that it's possible for you to custom design your investment portfolio in your 401k. And you get choices! Lots of them.

Depending on which investment bank is hosting your company's 401k program, you may have a variety of choices. Things like:
  * American Funds American Mutual R6
  * iShares MSCI EAFE Intl Idx K
  * (these are just examples -- NOT specific recommendations)
...and more.

And you ask yourself the inevitable question: which one are you supposed to choose? Oh wait. Not which one, but I can choose <i>more</i> than one?! And I have to choose what percentage of my contributions I want to allocate to each choice?

If you're like most people, including my wife (love you, darling) you toss your hands in the air, and select:
* Vanguard Target Retirement 20XX Inv
* (again -- not necessarily recommended here, though it's common)

And who's to blame you? Some of these investment banks offer twenty-five or more possible choices for you to allocate your nest-egg into. Who has time to research how you are supposed to diversify a 401k, which options help you meet your financial goals, and still leave enough time after your day job to enjoy your night life?

I agree with you. It's overwhelming. And then I did a six-month intensive coding bootcamp and dipped my toes into the world of data science, python programming, machine learning, and application development. And I thought: you know what would be cool, is to try and help everyone make better investment choices and hopefully make the world a better and more financially peaceful kind of place.

So welcome. Welcome to my answer to all of these dilemnas. And here comes my disclaimer: this is (see above) <i>my answer</i>. That doesn't mean it should be your answer. This is a free tool that provides some potential direction and insight. Is it based on the power of data science, analysis and machine learning? Yes. If you want to use my tool, and if it works for you, then that is awesome and I applaud your success. In a few seconds you'll get an answer kicked out, you can allocate your 401k, and you can smile and go live your life. I hope nothing more than to make your life a easier, and provide a bit of confidence that you're doing everything you can to build your future. If you have someone in your life that is way smarter than me and gives you better advice, I absolutely am in favor of you listening to them instead of me.

### General Investment Concepts and Understanding
The <i>way</i> oversimplified concept of retirement saving through an investment instrument like a 401k or Individual Retirement Account (IRA) is that you're just putting money aside that you are intending to use later on. We all kept piggy banks when we were young. The expectation of utilizing a retirement plan or account is that we're anticipating our savings to grow. You put your spare change in a jar every time you come home from the store. Eventually there is more than just a few cents. That's not growth. That's accumulation. Growth is you invest money into one of these instruments, and over time the $1 you invested becomes...more than a $1. Without you actually adding anything else into it. And as such what we need to evaluate is something you've undoubtedly heard of: return on investment (ROI).

So a clarifying point would be: to maximize ROI, you also need to evaluate everything that <i>effects</i> it. Remember math classes when you were young and how much you hated story problems? The difficult part of those problems was deciphering what all of your variables were and how to build the appropriate equation. Welcome. Back. Don't worry, there will be no exam. In this case you get a cheat sheet that just tells you the answers.

For the sake of argument, let's say you're going to invest ten percent of your earnings into retirement savings. If you make a median income in the United States of approximately $60,000/year, we can easily to calculate what 10% is going to be. One thing you may have to consider is if you want to invest <i>pre-tax</i> or <i>after-tax</i> income. A more in-depth discussion of the advantages of each, the opportunity for back-door conversions, and other related material is beyond the scope of this project. I would suggest you do your research on those things or discuss with a financial advisor what option may be best for you. For our purposes, we're just going to say you're investing $6,000 per year. A few additional simplifying assumptions:
  * You begin investing at age 30 (yeah, yeah, I know. it's just for illustrative purposes)
  * Your income never increases (probably very unlikely, but again...)
  * You <i>never</i> withdraw money from your investment accounts (look, I'm not your dad, but seriously...DON'T do this)
  * You retire at the age of 65 (maybe you're an aspiring FIRE, maybe you will work longer, again, illustrative purposes)
  * Your contributions to your retirement savings are evenly distributed throughout the year

In order to get from today to this calculated outcome, we have to build the equation. The money you contribute is your ten percent. Some factors add to it, while others reduce it:
  * Super-duper-basic ROI. You invested $6k in a mutual fund. You bought shares of that fund for $200/share. After exactly one year, the shares you purchased for $200 are now worth $208. Great! Your ROI is 4%. Remember, at 4% growth, you end up doubling your money from age 30 to age 65. Not bad. But it's not the only thing to consider.
  * Dividends. David-who? No, no...<i>dividends</i>. When you invest in a company that has positive income, sometimes (think big companies) they pay dividends. If your mutual fund is invested in these companies, guess where the dividend goes. INTO YOUR INVESTMENT PORTFOLIO. Yeah. It's used to buy additional shares in your allotted investment. The company just GIVES you money to get a larger share, so that you earn (passively) even more money! Dividends are cool.
  * Fees. Okay. So I'm not going to take this a certain route, but nothing is free. I know, sometimes, certain political groups like to pretend that they are or should be, but they're not. Some investment vehicles are self-aware enough to understand that they do a really good job investing your money. They're providing a quality service. There is a human doing that work. It requires way more complex calculation and understanding and research than what we're doing here. They deserve to be compensated for their work. So there's fees. We obviously don't love fees. But we do accept and understand them.
The goal then is to get a more educated equation for ROI: the growth of your investment over time, adding in the dividends you receive, and then accounting for the fees you have to pay. All of this is automated in your retirement savings account (RSA), but it is important for our purposes that you understand what all is going on. Because, our goal is to <i>maximize</i> this equation to your benefit.
  * G + D - F = R
  * R / P = ROI
Where G is the growth in value of your chosen investment over time, D are the dividends your portfolio receives, F are the fees taken from your portfolio, R is the total return your portfolio nets annually, and P is the beginning balance of your RSA annually.

Okay, so based on this, let's come up with some baselines: how much will you have in savings at age 65?
  * Amount <i>you</i> actually put away (saved) instead of spending: $ 216,000
  * Savings account at a bank earning 0.01% interest (gee, thanks): $ 216,389
  * Purchase a certificate of deposit, and consistently roll them over (and earn 2% interest annually): $ 314,966
  * Purchase savings bonds earning roughly 4%: $ 474,428
  * Invest in generic target retirement date mutual fund, earning about 6% interest: $ 734,783
  * Optimize your investment and either keep par or defeat the S&P 500: $ 2,118,383
Adjusted for typical inflation (we're going to throw our simplifying assumption here and not discuss 2022)
  * 

This is not rocket science. Most traditional financial advice/wisdom suggests that retired individuals withdraw approximately 4% of their retirement savings account balances annually. This withdraw is your retirement income. What does that equate to based on the above?:
  * Savings account: $ 10k per year (less than $1k per month). I hope social security didn't go bust.
  * Optimized investments: $ 85k per year. Umm. That's more than you made when you were WORKING! (see simplifying assumption)

So, are we good here? You good? Stop day dreaming. This is not a joke. We just turned a story problem into your own personal fantasy, fairy-tale on a beach, day drinking. Still hate math? Let's go make this work.

## Analysis and Challenges

### Gathering all of the data
Let's define in a bit more detail what we're trying to do. What we want is a tool to analyze all of the possible investment options that we might have in our 401k. This immediately presents two issues.
1. Which mutual funds are we going to analyze?
2. What metrics are we going to use to analyze performance?
3. Where do we get the data for each mutual fund so that we can perform analysis?
4. How do we know we can trust this data and be confident in the outcome of what is essentially a forecast model?

One. problem. at a time. Okay (deep breath).

In order to know which mutual funds to analyze (and eventually which ones to suggest), we have to have a complete list. In this original version of this tool, you will provide the symbols of the mutual funds available to you for investing. Over time, I may scope this tool to learn what options are available at a variety of banks, but these things may change from time to time, so it's best that you make sure we have an accurate list.



### Analysis of Outcomes Based on Challenges and Goals

### Challenges and Difficulties Encountered

## Results
