import './App.css';
import RatesTable from './components/RatesTable';

function App() {
  return (
  <div className='App'>
    <RatesTable data_url='https://storage.googleapis.com/uo-hotels-store/UO_Hotels.csv'/>
  </div>
  );
}

export default App;
