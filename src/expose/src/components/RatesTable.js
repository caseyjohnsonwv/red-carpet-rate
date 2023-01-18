import React, { useState, useEffect } from 'react';
import hash from 'object-hash';
import { readRemoteFile } from 'react-papaparse';
import RateRow from './RateRow';

function RatesTable({data_url}) {

    const [csvData, setCsvData] = useState(null);
    const [tableHeaders, setTableHeaders] = useState(null);


   // Retrieve CSV from Google Cloud on page load
    function loadCsvData(remote_url) {
        readRemoteFile(remote_url, {
            complete: (res) => {
                let newTableHeaders = res.data[0];
                let newCsvData = res.data.slice(1, undefined);
                setTableHeaders(newTableHeaders);
                setCsvData(newCsvData);
            }
        });
    }
    useEffect(() => loadCsvData(data_url), [data_url]);


    return (
        tableHeaders === null
        ? <></>
        : <>
            <table>
                <thead>
                    <tr key={hash(tableHeaders)}><RateRow data_row={tableHeaders} is_header_row={true}/></tr>
                </thead>
                <tbody>
                    {csvData.map(row => <tr key={hash(row)}><RateRow data_row={row}/></tr>)}
                </tbody>
            </table>
        </>
    );
}

export default RatesTable;
