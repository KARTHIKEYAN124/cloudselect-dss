export async function api<T>(path:string, body?:unknown):Promise<T> {
  const res = await fetch(`/api/${path}`, body === undefined ? undefined : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`)
  return data
}
export function download(name:string, contents:string, type='application/json') {
  const url=URL.createObjectURL(new Blob([contents],{type})); const a=document.createElement('a'); a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)
}
