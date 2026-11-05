/* URL-only feature extraction. Keep ordering and logic aligned with src/urlsentry/features.py. */
(function(root){
 const FEATURES=["url_length","hostname_length","path_length","query_length","dot_count","subdomain_count","hyphen_count","at_count","digit_ratio","letter_ratio","special_ratio","has_ip_host","https_scheme","https_in_text","suspicious_token_count","encoded_char_count","double_slash_path","port_present"];
 const tokenPattern=/(?:login|verify|account|secure|update|bank|signin|confirm|password|wallet)/gi;
 function featuresFor(value){
  const raw=value.trim(), candidate=raw.includes("://")?raw:`http://${raw}`;
  let u,host="",path="/",query="",portPresent=false;
  try{u=new URL(candidate);host=u.hostname.toLowerCase().replace(/\.$/,"");path=u.pathname||"/";query=u.search.startsWith("?")?u.search.slice(1):u.search;const authority=candidate.match(/^[a-z][a-z0-9+.-]*:\/\/([^/?#]*)/i)?.[1]?.split("@").pop()||"";portPresent=authority.startsWith("[") ? /\]:\d+$/.test(authority) : /:\d+$/.test(authority)}catch{u={protocol:"http:"}}
  const total=Math.max(raw.length,1),count=(s,re)=>[...s.matchAll(re)].length;
  const digits=count(raw,/[0-9]/g),letters=count(raw,/[A-Za-z]/g),alnum=count(raw,/[A-Za-z0-9]/g),special=raw.length-alnum;
  const bareHost=host.replace(/^\[|\]$/g,"");
  const ip=/^(?:\d{1,3}\.){3}\d{1,3}$/.test(bareHost)||bareHost.includes(":");
  const labels=host.split(".").filter(Boolean);
  return [raw.length,host.length,path.length,query.length,(host.match(/\./g)||[]).length,Math.max(0,labels.length-2),(raw.match(/-/g)||[]).length,(raw.match(/@/g)||[]).length,digits/total,letters/total,special/total,ip?1:0,u.protocol.toLowerCase()==="https:"?1:0,raw.toLowerCase().includes("https")?1:0,count(raw,tokenPattern),count(raw,/%/g),path.slice(1).includes("//")?1:0,portPresent?1:0];
 }
 const api={FEATURES,featuresFor}; if(typeof module!=="undefined"&&module.exports)module.exports=api; else root.URLSentryFeatures=api;
})(globalThis);
