import Image from 'next/image'
import Link from 'next/link'



export default function Home() {

  function fetchData() {
    console.log("hello");
  }

  
  return (
    <main className="homepage">
      <div className="nav">
        <h1 className="title" >NBA Wizard</h1>
        <Image src="/logo.png" alt="basketball" width={100} height={100}/>
      </div>
      <p>We pick it you hit it!</p>
   
      <button onClick={fetchData}>Fetch Recent Picks</button>
      
      
    </main>
  )
}
