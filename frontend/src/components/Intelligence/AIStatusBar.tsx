import React from 'react';
import {
 Cpu,
 Activity
} from 'lucide-react';


interface Props {
  isActive:boolean;
  lastUpdate:string;
}


export const AIStatusBar:React.FC<Props> = ({
 isActive,
 lastUpdate
})=>{


return (
<header className="
bg-dark-card
border-b
border-dark-border
rounded-xl
p-4
">


<div className="flex justify-between items-center">


<div className="flex items-center gap-3">

<Cpu className="text-blue-400"/>

<div>
<h2 className="font-bold text-white">
NEMESIS AI COMMAND CENTER
</h2>

<p className="text-xs text-gray-400">
Intelligence Monitoring System
</p>

</div>

</div>



<div className="text-right">

<div className={
`
flex items-center gap-2
${isActive?'text-green-400':'text-red-400'}
`
}>

<Activity size={16}/>

{isActive
?'AI ONLINE'
:'AI OFFLINE'
}

</div>


<p className="text-xs text-gray-500">
{
new Date(lastUpdate)
.toLocaleString('id-ID')
}
</p>


</div>


</div>

</header>

)

};


export default AIStatusBar;