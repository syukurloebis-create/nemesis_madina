interface Props{

data:any;

onOpen:()=>void;

}


export default function RecoveryWidget({
 data,
 onOpen
}:Props){


return (

<div
className="
rounded-xl
border
p-5
bg-green-50
cursor-pointer
"
onClick={onOpen}
>


<h3>
Recovery Intelligence
</h3>


<div>
Status:
{data?.recovery?.status}
</div>


<div>
Recoverable:
Rp
{data?.recovery?.recoverable_amount}
</div>


<button>
Open Recovery
</button>


</div>

)

}