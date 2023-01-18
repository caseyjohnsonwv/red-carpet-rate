import hash from 'object-hash';

function RateRow({data_row, is_header_row}) {
    return (
        <>{
            is_header_row === true
            ? data_row.map(val => <th key={hash(data_row.push(val))}>{val}</th>)
            : data_row.map(val => <td key={hash(data_row.push(val))}>{val}</td>)
        }</>
    );
}

export default RateRow;
