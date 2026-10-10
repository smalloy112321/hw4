import { Link } from 'react-router-dom'

export default function About() {
  return (
    <section className="section prose">
      <h1>About Us</h1>
      <p className="lead">
        Campus Customs is a New Haven shop built around one idea: Bulldog pride should be easy to
        wear, easy to give, and comfortable enough to live in.
      </p>

      <h2>Made for every kind of Bulldog</h2>
      <p>
        Our customers are first-years buying their first Yale hoodie, seniors picking up a
        class-year tee, alumni who come back for The Game, and parents and grandparents who want to
        cheer just as loudly. We design our collection with all of them in mind.
      </p>

      <h2>Comfort first, spirit always</h2>
      <p>
        We focus on the pieces people actually reach for: soft fleece, everyday crewnecks,
        quarter-zips that work from the stands to the office, and tees made for long game days. Each
        design is officially licensed, so the Yale name and marks are the real thing.
      </p>

      <h2>Here to help</h2>
      <p>
        Not sure about sizing, colors, or the right gift? Ask our chat in the bottom corner of any
        page. It checks our current catalogue for real prices and stock.
      </p>

      <p>
        <Link to="/products" className="btn">Browse the collection</Link>
      </p>
    </section>
  )
}
