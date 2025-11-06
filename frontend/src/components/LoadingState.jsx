export default function LoadingState({ message = "Carregando dados..." }) {
  return (
    <div className="flex items-center justify-center rounded-lg bg-white p-6 text-sm text-slate-500 shadow-sm ring-1 ring-slate-200">
      <svg
        className="mr-3 h-5 w-5 animate-spin text-primary"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
        ></path>
      </svg>
      {message}
    </div>
  );
}
